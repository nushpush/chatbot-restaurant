import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import BouncingDotsLoader from "../Loader/BouncingDotLoader"; // Adjust the path as necessary

describe("BouncingDotsLoader Component", () => {
  test("renders the loader with three bouncing dots", () => {
    // Render the component (no need for manual act)
    render(<BouncingDotsLoader />);
    
    // Find the container with the className 'bouncing-loader'
    const loaderContainer = screen.getByRole("presentation", { hidden: true });
    expect(loaderContainer).toBeInTheDocument();
    
    // Check if three child div elements are present inside the loader
    expect(loaderContainer.childNodes.length).toBe(3);
  });

  test("has the correct class name for loader animation", () => {
    render(<BouncingDotsLoader />);
    
    const loaderContainer = screen.getByRole("presentation", { hidden: true });
    expect(loaderContainer).toHaveClass("bouncing-loader");
  });
});
